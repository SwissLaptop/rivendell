// edit_cast.cpp
//
// Edit a Rivendell Cast
//
//   (C) Copyright 2002-2019 Fred Gleason <fredg@paravelsystems.com>
//
//   This program is free software; you can redistribute it and/or modify
//   it under the terms of the GNU General Public License version 2 as
//   published by the Free Software Foundation.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.
//
//   You should have received a copy of the GNU General Public
//   License along with this program; if not, write to the Free Software
//   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
//

#include <qradiobutton.h>

#include <rdconf.h>
#include <rddatedialog.h>

#include "edit_cast.h"
#include "globals.h"
#include "pick_report_dates.h"

EditCast::EditCast(unsigned cast_id,QWidget *parent)
  : RDDialog(parent)
{
  int ypos=0;

  cast_cast=new RDPodcast(rda->config(),cast_id);
  cast_feed=new RDFeed(cast_cast->feedId(),rda->config());
  cast_status=cast_cast->status();
  setWindowTitle("RDCastManager - "+tr("Editing PodCast"));

  //
  // Item Media Link
  //
  cast_item_medialink_edit=new QLineEdit(this);
  cast_item_medialink_edit->setGeometry(135,10,sizeHint().width()-145,20);
  cast_item_medialink_edit->setReadOnly(true);
  QLabel *cast_item_medialink_label=
    new QLabel(cast_item_medialink_edit,tr("Media Link:"),this);
  cast_item_medialink_label->setGeometry(20,10,110,20);
  cast_item_medialink_label->setFont(labelFont());
  cast_item_medialink_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);
  if(cast_feed->mediaLinkMode()==RDFeed::LinkNone) {
    cast_item_medialink_edit->hide();
    cast_item_medialink_label->hide();
    ypos=10;
  }
  else {
    ypos=42;
  }

  //
  // Item Title
  //
  cast_item_title_edit=new QLineEdit(this);
  cast_item_title_edit->setGeometry(135,ypos,sizeHint().width()-145,20);
  cast_item_title_edit->setMaxLength(255);
  QLabel *cast_item_title_label=
    new QLabel(cast_item_title_edit,tr("Title:"),this);
  cast_item_title_label->setGeometry(20,ypos,110,20);
  cast_item_title_label->setFont(labelFont());
  cast_item_title_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Author
  //
  cast_item_author_edit=new QLineEdit(this);
  cast_item_author_edit->setGeometry(135,ypos+22,sizeHint().width()-145,20);
  cast_item_author_edit->setMaxLength(255);
  QLabel *cast_item_author_label=
    new QLabel(cast_item_author_edit,tr("Author E-Mail:"),this);
  cast_item_author_label->setGeometry(20,ypos+22,110,20);
  cast_item_author_label->setFont(labelFont());
  cast_item_author_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Category
  //
  cast_item_category_edit=new QLineEdit(this);
  cast_item_category_edit->setGeometry(135,ypos+44,sizeHint().width()-145,20);
  cast_item_category_edit->setMaxLength(64);
  QLabel *cast_item_category_label=
    new QLabel(cast_item_category_edit,tr("Category:"),this);
  cast_item_category_label->setGeometry(20,ypos+44,110,20);
  cast_item_category_label->setFont(labelFont());
  cast_item_category_label->
    setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Link
  //
  cast_item_link_edit=new QLineEdit(this);
  cast_item_link_edit->setGeometry(135,ypos+66,sizeHint().width()-145,20);
  cast_item_link_edit->setMaxLength(255);
  QLabel *cast_item_link_label=
    new QLabel(cast_item_link_edit,tr("Link URL:"),this);
  cast_item_link_label->setGeometry(20,ypos+66,110,20);
  cast_item_link_label->setFont(labelFont());
  cast_item_link_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Description
  //
  cast_item_description_edit=new QTextEdit(this);
  cast_item_description_edit->
    setGeometry(135,ypos+88,sizeHint().width()-145,76);
  QLabel *cast_item_description_label=
    new QLabel(cast_item_description_edit,tr("Description:"),this);
  cast_item_description_label->setGeometry(20,ypos+88,110,20);
  cast_item_description_label->setFont(labelFont());
  cast_item_description_label->
    setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Source Text
  //
  cast_item_sourcetext_edit=new QLineEdit(this);
  cast_item_sourcetext_edit->
    setGeometry(135,ypos+169,sizeHint().width()-145,20);
  cast_item_sourcetext_edit->setMaxLength(64);
  QLabel *cast_item_sourcetext_label=
    new QLabel(cast_item_sourcetext_edit,tr("Source Text:"),this);
  cast_item_sourcetext_label->setGeometry(20,ypos+169,110,20);
  cast_item_sourcetext_label->setFont(labelFont());
  cast_item_sourcetext_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Source URL
  //
  cast_item_sourceurl_edit=new QLineEdit(this);
  cast_item_sourceurl_edit->setGeometry(135,ypos+191,sizeHint().width()-145,20);
  cast_item_sourceurl_edit->setMaxLength(64);
  QLabel *cast_item_sourceurl_label=
    new QLabel(cast_item_sourceurl_edit,tr("Source URL:"),this);
  cast_item_sourceurl_label->setGeometry(20,ypos+191,110,20);
  cast_item_sourceurl_label->setFont(labelFont());
  cast_item_sourceurl_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  //
  // Item Comments
  //
  cast_item_comments_edit=new QLineEdit(this);
  cast_item_comments_edit->setGeometry(135,ypos+213,sizeHint().width()-145,20);
  cast_item_comments_edit->setMaxLength(64);
  QLabel *cast_item_comments_label=
    new QLabel(cast_item_comments_edit,tr("Comments URL:"),this);
  cast_item_comments_label->setGeometry(10,ypos+213,120,20);
  cast_item_comments_label->setFont(labelFont());
  cast_item_comments_label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);

  cast_ypos=233+ypos;

  //
  // Effective DateTime
  //
  cast_item_effective_edit=new QDateTimeEdit(this);
  cast_item_effective_edit->
    setGeometry(135,cast_ypos,165,20);
  QLabel *label=new QLabel(cast_item_effective_edit,tr("Air Date/Time:"),this);
  label->setGeometry(20,cast_ypos,110,20);
  label->setFont(labelFont());
  label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);
  QPushButton *button=new QPushButton(this);
  button->setGeometry(310,cast_ypos,50,20);
  button->setFont(subButtonFont());
  button->setText(tr("&Select"));
  connect(button,SIGNAL(clicked()),this,SLOT(effectiveSelectData()));
  cast_ypos+=22;

  //
  // Item Origin
  //
  cast_item_origin_edit=new QLineEdit(this);
  cast_item_origin_edit->setReadOnly(true);
  cast_item_origin_edit->setGeometry(135,cast_ypos,165,20);
  cast_item_origin_edit->setMaxLength(64);
  QLabel *cast_item_origin_label=
    new QLabel(cast_item_origin_edit,tr("Posted At:"),this);
  cast_item_origin_label->setGeometry(20,cast_ypos,110,20);
  cast_item_origin_label->setFont(labelFont());
  cast_item_origin_label->
    setAlignment(Qt::AlignRight|Qt::AlignVCenter);
  cast_ypos+=22;

  //
  // Item Expiration
  //
  cast_item_expiration_box=new QComboBox(this);
  cast_item_expiration_box->setGeometry(135,cast_ypos,50,20);
  cast_item_expiration_box->insertItem(tr("No"));
  cast_item_expiration_box->insertItem(tr("Yes"));
  connect(cast_item_expiration_box,SIGNAL(activated(int)),
	  this,SLOT(expirationSelectedData(int)));
  label=new QLabel(cast_item_expiration_box,tr("Cast Expires:"),this);
  label->setGeometry(20,cast_ypos,110,20);
  label->setFont(labelFont());
  label->
    setAlignment(Qt::AlignRight|Qt::AlignVCenter);
  cast_ypos+=22;
  cast_item_expiration_box->setEnabled(cast_status!=RDPodcast::StatusExpired);
  label->setEnabled(cast_status!=RDPodcast::StatusExpired);

  cast_item_expiration_edit=new QDateEdit(this);
  cast_item_expiration_edit->setGeometry(135,cast_ypos,95,20);
  cast_item_expiration_label=
    new QLabel(cast_item_expiration_edit,tr("Expires On:"),this);
  cast_item_expiration_label->setGeometry(20,cast_ypos,110,20);
  cast_item_expiration_label->setFont(labelFont());
  cast_item_expiration_label->
    setAlignment(Qt::AlignRight|Qt::AlignVCenter);
  cast_item_expiration_button=new QPushButton(this);
  cast_item_expiration_button->setGeometry(240,cast_ypos,50,20);
  cast_item_expiration_button->setFont(subButtonFont());
  cast_item_expiration_button->setText(tr("&Select"));
  connect(cast_item_expiration_button,SIGNAL(clicked()),
	  this,SLOT(expirationSelectData()));
  cast_ypos+=27;
  cast_item_expiration_edit->setEnabled(cast_status!=RDPodcast::StatusExpired);
  cast_item_expiration_label->
    setEnabled(cast_status!=RDPodcast::StatusExpired);
  cast_item_expiration_button->
    setEnabled(cast_status!=RDPodcast::StatusExpired);

  //
  // Cast Status
  //
  cast_item_status_group=new QButtonGroup(this);
  cast_item_status_group->setExclusive(true);
  //  cast_item_status_group->hide();

  QRadioButton *rbutton=new QRadioButton(this);
  rbutton->setGeometry(140,cast_ypos,15,15);
  cast_item_status_group->addButton(rbutton,0);
  label=new QLabel(rbutton,tr("Hold"),this);
  label->setFont(subButtonFont());
  label->setGeometry(160,cast_ypos,30,15);
  label->setAlignment(Qt::AlignVCenter|Qt::AlignLeft);
  rbutton->setChecked(true);
  label->setEnabled(cast_status!=RDPodcast::StatusExpired);
  rbutton->setEnabled(cast_status!=RDPodcast::StatusExpired);

  rbutton=new QRadioButton(this);
  rbutton->setGeometry(210,cast_ypos,15,15);
  cast_item_status_group->addButton(rbutton,1);
  label=new QLabel(rbutton,tr("Active"),this);
  label->setFont(subLabelFont());
  label->setGeometry(230,cast_ypos,80,15);
  label->setAlignment(Qt::AlignVCenter|Qt::AlignLeft);
  label->setEnabled(cast_status!=RDPodcast::StatusExpired);
  label=new QLabel(tr("Posting Status:"),this);
  label->setGeometry(20,cast_ypos-1,110,20);
  label->setFont(labelFont());
  label->setAlignment(Qt::AlignRight|Qt::AlignVCenter);
  label->setEnabled(cast_status!=RDPodcast::StatusExpired);
  rbutton->setEnabled(cast_status!=RDPodcast::StatusExpired);

  //
  //  Report Button
  //
  button=new QPushButton(this);
  button->setGeometry(10,sizeHint().height()-60,80,50);
  button->setFont(buttonFont());
  button->setText(tr("Episode\n&Report"));
  connect(button,SIGNAL(clicked()),this,SLOT(reportData()));

  //
  //  Ok Button
  //
  button=new QPushButton(this);
  button->setGeometry(sizeHint().width()-180,sizeHint().height()-60,80,50);
  button->setDefault(true);
  button->setFont(buttonFont());
  button->setText(tr("&OK"));
  connect(button,SIGNAL(clicked()),this,SLOT(okData()));

  //
  //  Cancel Button
  //
  button=new QPushButton(this);
  button->setGeometry(sizeHint().width()-90,sizeHint().height()-60,
			     80,50);
  button->setFont(buttonFont());
  button->setText(tr("&Cancel"));
  connect(button,SIGNAL(clicked()),this,SLOT(cancelData()));

  //
  // Populate Values
  //
  cast_item_medialink_edit->
    setText(cast_feed->audioUrl(cast_feed->mediaLinkMode(),
				"[web-hostname]",cast_cast->id()));
  cast_item_title_edit->setText(cast_cast->itemTitle());
  cast_item_author_edit->setText(cast_cast->itemAuthor());
  cast_item_origin_edit->setText(RDUtcToLocal(cast_cast->originDateTime()).
				 toString("MM/dd/yyyy - hh:mm:ss"));
  cast_item_category_edit->setText(cast_cast->itemCategory());
  cast_item_link_edit->setText(cast_cast->itemLink());
  cast_item_sourcetext_edit->setText(cast_cast->itemSourceText());
  cast_item_sourceurl_edit->setText(cast_cast->itemSourceUrl());
  cast_item_description_edit->setText(cast_cast->itemDescription());
  cast_item_comments_edit->setText(cast_cast->itemComments());
  cast_item_effective_edit->
    setDateTime(RDUtcToLocal(cast_cast->effectiveDateTime()));
  if(cast_cast->shelfLife()>0) {
    cast_item_expiration_box->setCurrentItem(1);
  }
  cast_item_expiration_edit->
    setDate(RDUtcToLocal(cast_cast->originDateTime()).date().
	    addDays(cast_cast->shelfLife()));
  expirationSelectedData(cast_item_expiration_box->currentItem());
  switch(cast_status) {
  case RDPodcast::StatusActive:
    cast_item_status_group->button(1)->setChecked(true);
    break;

  case RDPodcast::StatusPending:
    cast_item_status_group->button(0)->setChecked(true);
    break;

  case RDPodcast::StatusExpired:
    cast_item_status_group->button(0)->setDisabled(true);
    cast_item_status_group->button(1)->setDisabled(true);
    break;
  }

  //
  // Fix the Window Size
  //
  setMinimumWidth(sizeHint().width());
  setMaximumWidth(sizeHint().width());
  setMinimumHeight(sizeHint().height());
  setMaximumHeight(sizeHint().height());
}


EditCast::~EditCast()
{
  delete cast_feed;
  delete cast_cast;
}


QSize EditCast::sizeHint() const
{
  return QSize(640,cast_ypos+92);
} 


QSizePolicy EditCast::sizePolicy() const
{
  return QSizePolicy(QSizePolicy::Fixed,QSizePolicy::Fixed);
}


void EditCast::expirationSelectedData(int state)
{
  state=state&&(cast_status!=RDPodcast::StatusExpired);
  cast_item_expiration_edit->setEnabled(state);
  cast_item_expiration_button->setEnabled(state);
  cast_item_expiration_label->setEnabled(state);
}


void EditCast::effectiveSelectData()
{
  QDate current_date=QDate::currentDate();
  QDateTime datetime=cast_item_effective_edit->dateTime();
  QDate date=datetime.date();

  RDDateDialog *dd=
    new RDDateDialog(current_date.year()-5,current_date.year()+5,this);
  if(dd->exec(&date)==0) {
    datetime.setDate(date);
    cast_item_effective_edit->setDateTime(datetime);
  }
  delete dd;
}


void EditCast::expirationSelectData()
{
  QDate current_date=QDate::currentDate();
  QDate date=cast_item_expiration_edit->date();
    
  RDDateDialog *dd=
    new RDDateDialog(current_date.year(),current_date.year()+10,this);
  if(dd->exec(&date)==0) {
    cast_item_expiration_edit->setDate(date);
  }
  delete dd;
}


void EditCast::reportData()
{
  PickReportDates *rd=new PickReportDates(cast_cast->feedId(),cast_cast->id());
  rd->exec();
  delete rd;
}


void EditCast::okData()
{
  cast_cast->setItemTitle(cast_item_title_edit->text());
  cast_cast->setItemAuthor(cast_item_author_edit->text());
  cast_cast->setItemCategory(cast_item_category_edit->text());
  cast_cast->setItemLink(cast_item_link_edit->text());
  cast_cast->setItemSourceText(cast_item_sourcetext_edit->text());
  cast_cast->setItemSourceUrl(cast_item_sourceurl_edit->text());
  cast_cast->setItemDescription(cast_item_description_edit->text());
  cast_cast->setItemComments(cast_item_comments_edit->text());
  cast_cast->
    setEffectiveDateTime(RDLocalToUtc(cast_item_effective_edit->dateTime()));
  if(cast_item_status_group->button(0)->isEnabled()) {
    if(cast_item_expiration_box->currentItem()) {
      int shelf_life=RDUtcToLocal(cast_cast->originDateTime()).date().
	daysTo(cast_item_expiration_edit->date());
      if(shelf_life<1) {
	shelf_life=1;
      }
      cast_cast->setShelfLife(shelf_life);
    }
    else {
      cast_cast->setShelfLife(0);
    }
    switch(cast_item_status_group->checkedId()) {
      case 0:
	cast_cast->setStatus(RDPodcast::StatusPending);
	break;
	
      case 1:
	cast_cast->setStatus(RDPodcast::StatusActive);
	break;
    }
  }

  cast_feed->
    setLastBuildDateTime(RDLocalToUtc(QDateTime(QDate::currentDate(),
						QTime::currentTime())));
  done(0);
}


void EditCast::cancelData()
{
  done(-1);
}
